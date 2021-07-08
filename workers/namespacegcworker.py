import logging
import time

import features

from app import app, namespace_gc_queue, all_queues
from data import model
from workers.queueworker import QueueWorker, WorkerSleepException
from util.log import logfile_path
from util.locking import GlobalLock, LockNotAcquiredException
from util.metrics.prometheus import gc_namespaces_purged

logger = logging.getLogger(__name__)


POLL_PERIOD_SECONDS = 60
NAMESPACE_GC_TIMEOUT = 3 * 60 * 60  # 3h
LOCK_TIMEOUT_PADDING = 60  # 60 seconds


class NamespaceGCWorker(QueueWorker):
    """
    Worker which cleans up namespaces enqueued to be GCed.
    """

    def process_queue_item(self, job_details):
        try:
            with GlobalLock(
                "LARGE_GARBAGE_COLLECTION", lock_ttl=NAMESPACE_GC_TIMEOUT + LOCK_TIMEOUT_PADDING
            ):
                self._perform_gc(job_details)
        except LockNotAcquiredException:
            logger.debug("Could not acquire global lock for garbage collection")
            raise WorkerSleepException

    def _perform_gc(self, job_details):
        logger.debug("Got namespace GC queue item: %s", job_details)
        marker_id = job_details["marker_id"]
        if not model.user.delete_namespace_via_marker(marker_id, all_queues):
            raise Exception("GC interrupted; will retry")

        gc_namespaces_purged.inc()


if __name__ == "__main__":
    logging.config.fileConfig(logfile_path(debug=False), disable_existing_loggers=False)

    if app.config.get("ACCOUNT_RECOVERY_MODE", False):
        logger.debug("Quay running in account recovery mode")
        while True:
            time.sleep(100000)

    if not features.NAMESPACE_GARBAGE_COLLECTION:
        logger.info("Namespace garbage collection is disabled; skipping")
        while True:
            time.sleep(100000)

    GlobalLock.configure(app.config)
    logger.debug("Starting namespace GC worker")
    worker = NamespaceGCWorker(
        namespace_gc_queue,
        poll_period_seconds=POLL_PERIOD_SECONDS,
        reservation_seconds=NAMESPACE_GC_TIMEOUT,
    )
    worker.start()

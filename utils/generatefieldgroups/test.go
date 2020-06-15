package fieldgroups

// Struct Definition
type TagExpirationFieldGroup struct {
	FeatureChangeTagExpiration bool
	DefaultTagExpiration       string
	TagExpirationOptions       []string
}

// Constructor
func NewTagExpirationFieldGroup(fullConfig map[string]interface{}) FieldGoup {

	var FeatureChangeTagExpiration_SET bool = false
	if value, ok := fullConfig["FEATURE_CHANGE_TAG_EXPIRATION"]; ok {
		FeatureChangeTagExpiration_SET = value
	}
	var DefaultTagExpiration_SET string = "2w"
	if value, ok := fullConfig["DEFAULT_TAG_EXPIRATION"]; ok {
		DefaultTagExpiration_SET = value
	}
	var TagExpirationOptions_SET []string
	if value, ok := fullConfig["TAG_EXPIRATION_OPTIONS"]; ok {
		TagExpirationOptions_SET = value
	}

	return &TagExpirationFieldGroup{
		DefaultTagExpiration:       DefaultTagExpiration_SET,
		TagExpirationOptions:       TagExpirationOptions_SET,
		FeatureChangeTagExpiration: FeatureChangeTagExpiration_SET,
	}
}

// Validator Function
func (fg *TagExpirationFieldGroup) Validate() (bool, error) {
	return true, nil
}

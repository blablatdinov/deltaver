use std::fmt;

#[derive(Debug, Clone)]
pub struct Package {
    pub name: String,
    pub version: String,
    pub release_date: chrono::NaiveDate,
}

impl Package {
    pub fn new(name: String, version: String, release_date: chrono::NaiveDate) -> Self {
        Self {
            name,
            version,
            release_date,
        }
    }

    pub fn name(&self) -> &str {
        &self.name
    }

    pub fn is_prerealese(&self) -> bool {
        self.version.contains("alpha")
            || self.version.contains("beta")
            || self.version.contains("rc")
            || self.version.contains("dev")
    }
}

impl fmt::Display for Package {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}=={} ({})", self.name, self.version, self.release_date)
    }
}

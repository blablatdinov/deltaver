pub mod package;
pub use package::Package;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Ecosystem {
    PyPi,
    NPM,
    Hex,
    Go,
}

impl Ecosystem {
    pub fn name(&self) -> &'static str {
        match self {
            Ecosystem::PyPi => "PyPi",
            Ecosystem::NPM => "NPM",
            Ecosystem::Hex => "Hex",
            Ecosystem::Go => "Go",
        }
    }
}

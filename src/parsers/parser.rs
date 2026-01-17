use crate::core::Package;
use anyhow::Result;

pub trait Parser {
    fn reqs(&self) -> Result<Vec<Package>>;
}

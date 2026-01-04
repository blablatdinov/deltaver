pub fn parse_dependency_line(line: &str) -> Option<(String, String)> {
    let line = line.trim();
    if line.is_empty() || line.starts_with('#') {
        return None;
    }
    let parts: Vec<&str> = line.split("==").collect();
    if parts.len() != 2 {
        return None;
    }
    let name = parts[0].trim().to_string();
    let version = parts[1].trim().to_string();
    if name.is_empty() || version.is_empty() {
        return None
    }
    Some((name, version))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_dependency_line() {
        assert_eq!(
            parse_dependency_line("httpx==0.25.0"),
            Some(("httpx".to_string(), "0.25.0".to_string()))
        )
    }
}
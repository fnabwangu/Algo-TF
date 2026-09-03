def should_replace(
	*, quote_age_seconds: float, maximum_quote_age_seconds: float, elapsed_seconds: float,
	replace_interval_seconds: float, replacements: int, maximum_replacements: int,
) -> bool:
	return (
		quote_age_seconds <= maximum_quote_age_seconds
		and elapsed_seconds >= replace_interval_seconds
		and replacements < maximum_replacements
	)

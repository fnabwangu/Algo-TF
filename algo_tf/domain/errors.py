class AlgoTfError(Exception):
	"""Base class for expected runtime failures."""


class MandateViolation(AlgoTfError):
	pass


class StaleDataError(AlgoTfError):
	pass


class KillSwitchActive(AlgoTfError):
	pass

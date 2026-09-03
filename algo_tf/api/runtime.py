from __future__ import annotations

from algo_tf.persistence.database import Database
from algo_tf.persistence.repositories.audit_repository import AuditRepository
from algo_tf.persistence.repositories.decision_repository import DecisionRepository
from algo_tf.persistence.repositories.intent_repository import IntentRepository
from algo_tf.persistence.repositories.mandate_repository import MandateRepository
from algo_tf.persistence.repositories.observation_repository import ObservationRepository
from algo_tf.services.execution_monitor import ExecutionMonitor
from algo_tf.services.observation_service import ObservationService

database = Database()
mandates = MandateRepository(database)
observations = ObservationService(ObservationRepository(database))
decisions = DecisionRepository(database)
intents = IntentRepository(database)
audit = AuditRepository(database)
execution_monitor = ExecutionMonitor()

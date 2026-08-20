from types import SimpleNamespace

from training.handlers.training.corpus_training_handler import CorpusTrainingHandler


def test_collects_one_validation_loss_per_epoch() -> None:
    trainer = SimpleNamespace(
        state=SimpleNamespace(
            log_history=[
                {"epoch": 1.0, "eval_loss": 3.1},
                {"epoch": 2.0, "eval_loss": 2.7},
                {"epoch": 3.0, "eval_loss": 2.5},
                {"epoch": 3.0, "eval_loss": 2.4},
            ]
        )
    )
    handler = CorpusTrainingHandler(None, None, None, None, None, None)

    assert handler._epoch_eval_metrics(trainer) == [
        {"epoch": 1.0, "eval_loss": 3.1},
        {"epoch": 2.0, "eval_loss": 2.7},
        {"epoch": 3.0, "eval_loss": 2.4},
    ]

.PHONY: clean setup-phase-0 setup

clean:
	rm -f events.db .lock

setup-phase-0: clean
	python scripts/migrate.py
	python scripts/seed_phase_0.py

setup: setup-phase-0
LIMIT ?= '*'

install:
	@uv sync --refresh --extra dev
	@uv pip install -e .[dev]

clean:
	@rm -rf .env.inventory *.log *.lock *.egg-info build/

cf:
	@uv run pyinfra -y inventories/home.py --data apply_dns=True deploy_home.py

infra.%:
	@uv run pyinfra -y --limit $(LIMIT) \
		inventories/$(shell echo $(@) | cut -d. -f2).py \
		deploy_$(shell echo $(@) | cut -d. -f2).py

uninfra.%:
	@uv run pyinfra -y --limit $(LIMIT) --data teardown=True \
		inventories/$(shell echo $(@) | cut -d. -f2).py \
		deploy_$(shell echo $(@) | cut -d. -f2).py

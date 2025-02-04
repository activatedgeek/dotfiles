LIMIT ?= '*'

install:
	@rm -f uv.lock
	@uv sync -U --refresh --extra dev
	@uv pip install -e .[dev]

clean:
	@rm -rf .env.inventory *.log *.lock *.egg-info build/

infra.%:
	@uv run pyinfra -y --limit $(LIMIT) \
		inventories/$(shell echo $(@) | cut -d. -f2).py \
		deploy_$(shell echo $(@) | cut -d. -f2).py

uninfra.%:
	@uv run pyinfra -y --limit $(LIMIT) --data teardown=True \
		inventories/$(shell echo $(@) | cut -d. -f2).py \
		deploy_$(shell echo $(@) | cut -d. -f2).py

dns:
	@uv run pyinfra -y --limit mac --data apply_dns=True \
		inventories/home.py \
		tasks/cloudflare.py

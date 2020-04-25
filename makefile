EXAMPLES:=$(wildcard examples/*.cm)

examples/%.svg: examples/%.cm
	python -m circuit_markup $^ $@

examples: $(patsubst %.cm,%.svg,$(EXAMPLES))

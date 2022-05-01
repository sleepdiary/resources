build: entities.json thumbs

entities.json: bin/compile-entities.js entities/*/*.json software-thumbs/*
	./$<

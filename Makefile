build: entities.json thumbs

entities.json: compile-entities.js entities/*.yaml software-thumbs/*
	./$<

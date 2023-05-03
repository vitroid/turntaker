deploy:
	fly launch --now

debug:
	uvicorn main:app

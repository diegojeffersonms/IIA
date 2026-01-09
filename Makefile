.PHONY: up down restart

# Sobe os containers e abre o navegador
up:
	docker compose up -d
	@echo "Aguardando inicialização..."
	@sleep 5
	@python3 -m webbrowser http://localhost:8080

# Desliga tudo
down:
	docker compose down

# Reinicia e reconstrói (útil quando você mexe no plugin JS)
build:
	docker compose up -d --build
	@sleep 5
	@python3 -m webbrowser http://localhost:8080
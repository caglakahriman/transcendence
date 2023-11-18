all:
	docker-compose -f docker-compose.yml up
clean:
	docker-compose -f docker-compose.yml down
fclean: clean
	docker system prune -a --force
	docker volume prune -a --force
	rm -rf ./postgres_data

re: fclean all

.PHONY: all clean fclean re
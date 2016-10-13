.PHONY: geodata, meetup_data, total_numbers

#################################################################################
# GLOBALS                                                                       #
#################################################################################

#################################################################################
# COMMANDS                                                                      #
#################################################################################

requirements:
	pip install -q -r requirements.txt

geodata: requirements
	python src/data/make_geodata.py

meetup_data: requirements
	python src/data/get_data.py

event_data: meetup_data
	python -m src.data.get_group_activities

total_numbers:
	python src/data/sum_data.py

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################

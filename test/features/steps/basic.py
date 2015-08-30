from behave import given, when, then

import os, sys
import subprocess

from behave_utils import ( setup_testing_environment, check_id_exists_in_db,
						   run_script_and_get_id )


@given('we have recipy set up for testing')
def step_impl(context):
    context.db_file = setup_testing_environment("/Users/robin/code/recipy/test/scratch/")

@when('we run some code')
def step_impl(context):
    context.run_id = run_script_and_get_id('example_script2.py')

@then('an entry should be added to the database')
def step_impl(context):
	check_id_exists_in_db(context.run_id, context.db_file)
# Rulebook
  - Validate and revise Pandas dataframes

# Status
  - alpha 
  - Will change, everything does not work well, use at your own risk

# Usage
```python
    import rulebook as rb
    
    # create a rulebook
    rules=rb.RuleBook()
    
    # add rules to the rulebook
    rules.add('age>0') # add one rule for one column
    rules.add('no_missing', cols=['id_n', 'date', 'cost']) # use a predefined rule for many columns
    
    # check the dataframe against the rules
    rules.check(df)
```
    
# Features
  - Succinct: Easy to add many rules to many columns
  - Flexible: Use predefined rules or add your own functions or expressions
  - Smart: A method to suggest rules save you work of generating rules
  - Sharable: The rulebook can be saved and shared
  - Visualize: Get a quick visualization of amount and type of invalid data
  
# Installation
```python pip install rulebook```
    
# Requirements
  - Python 3.6 and above
  - Pandas
  
# Licence
  -MIT
  
# Advanced features
  - Add complex rule expressions (pandas expressions) ```python # All observations with the same id should also have the same gender
 rules.add("df.groupby('id')['gender'].nunique()<2")```        
  - Rules for revising invalid data 
  ```python 
  # Make all values that are invalid, missing
      rules.add("isin('m', 'f')", cols='gender', invalid='to_missing')
  # Check and revise the dataframe
      revised_df = rules.check_and_revise(df)
 ```  

# General structure
  - There are three types of rules that can be added:
    - Expressions
      - Simple: rules.add('age>25')
      - Logical: No pregnant men: rules.add("not (gender=='m' and icd=='O82)")
    - Functions
      - Pre-defined: rules.add(['never_negative', 'never_missing'], cols=['id', 'age'])
      - Self-defined: rules.add('THE_NAME_OF_YOUR_FUNCTION') 
          Define a function that takes a dataframe (and possibly a column) and returns a series that is True or False. The name of the function can be added as a rule:
    - Pandas expressions
      - Series: rules.add("name.str.contains('Cathy')")
      - Datafrmme:       
      ```python
      # For each persons age should never decrease as the date increases
       rules.add("df.sort_values(['id', 'age']).groupby('id')['age'].is_monotonic")```
     
 # API info
  - rules=rb.RuleBook()
  - rules.add()
  - rules.delete()
  - rules.view()
  - rules.check()
  - rules.check_and_revise()
  - rules.save()
  - rb.load()
  - rb.suggest_rules()
  
 
    
    
  
  

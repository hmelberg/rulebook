import pandas as pd
import snotra as sa
#%%
path=r'D:/ibd/1995/'
#path=r'E:/ibd/1995/'

#npr = pd.read_pickle(path + 'npr1995ibdv4.p')
#gp = pd.read_pickle('D:/ibd/1995/kuhr_2006to2017v2.p')
#rx = pd.read_pickle(path+'rx1995ibdv3.p')

#path=r'D:/ibd/1995/'
npr=pd.read_pickle(path + 'npr_ibd_selected v2.p')

#mdf=pd.read_pickle(path+ 'merged_rx_npr_v4nb.p')

#%%

df=npr.sample_persons().copy()

#%%

from rulebook.main import *
from rulebook.validators import *

#%%
rb = RuleBook()
#%%
rb.view()
a=rb.check(df)
df.year

rb.save('rb1.pickle')

rb =load_rulebook("rb1.pickle")
del rb
rb
df2=rb.change(df=df)

rb.add('age>0', cols='age')
rb.add('year<2016', cols='year')


rb.add("df.groupby('pid')['gender'].nunique()<2", cols='gender')
rb.add("gender == ['Mann', 'Kvinne']", cols='gender', action="to_nan")

df.gender.value_counts()


rb.add('is_int', cols='age', action="to_nan")


rb.add(['is_int', 'is_positive'], cols='age, pid')

rb.view()

rb.check(df)

rb.add('is_int', cols='age, pid')
rb.add('stable', cols='gender, byear')

rb.add("one_of(valid=@icd)", 'gender')


globals()['is_int']



def stable(df, col, pid='pid'):
    ok = df.groupby(pid)[col].nunique()<2
    return ok








rb.add("days<50")

rb.add("one_of(valid=['Mann', 'Kvinne'])", 'gender')
rb.view()
a=rb.check(df)
a
len(df)

rb.add("one_of(valid=['Mann', 'Kvinne'])", 'gender')

rb.add("""evaluate(expression="df.gender.isin(['Mann', 'Kvinne']"""))


df.columns
rb.add(')
rb.add("gender.isin['Mann', 'Kvinne']")
rb.add("df.groupby('pid').gender.nunique()<2")
rb.add("df.gender.isin['Mann', 'Kvinne']")


rb.add("df.age>0")

rb.add("df['age']>0")


rb.add("days<50")

rb.add("df.days<50")


rb.add("(age == age) and (age>0)")


a[('rule_1_sub_0',)].days

(df.days>=50).sum()
df.days<50

rb.add("""evaluate(expr="df.groupby('pid')['gender'].nunique()<2")""")

rb.add("df.groupby('pid')['gender'].nunique()<2")



rb.add("one_of(valid=['Mann', 'Kvinne'])", 'gender')


a.keys()
a

# with eval, can say rb.add("one_of(['Mann', 'Kvinne'])", 'gender')
# add(gender is one_of Mann, Kvinne)

df.gender.isin(['Mann', 'Kvinne'])


rb=RuleBook()
rb.add('is_int', 'age')
rb
rb.view()

rb.rule_1.rules
rb.rule_1.cols
rb.rulebook_list
rb.rulebook_list[0].cols



a=group2rules(rb.rule_1)
a[0].func
a[0].name
a[0].group
a[0].group
print(a[0].args)
a

b=_expand_rules(rb)

b
b[0].func
b[0].args


rb=RuleBook()
rb.add('is_int', ['age', 'pid'])
rb.view()





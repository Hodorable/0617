import PolicyUI_Model
policy=PolicyUI_Model.PolicyUI_Model()
obj=policy.PolicyUI_gets()
datas=""
for o in obj:
    datas+=o.name+"&"+o.objects+"&"+o.vi_condition+"&"+o.actions+"&"+o.data+"@@"
print datas



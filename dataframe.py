import pandas

# df = pandas.read_csv('files/pred.csv')
#
# y = df['预计黄金涨幅'].to_list()
# aa = df['预计比特币涨幅'].to_list()
# y_new = []
# aa_new = []
# current = 0
# current_a = 0
#
# for i in range(0, len(y)):
#     current = current + y[i]
#     current_a = current_a + aa[i]
#     y_new.append(current)
#     aa_new.append(current_a)
#
# df['pred_gold_inc_rate'] = y_new
# df['pred_bit_inc_rate'] = aa_new
#
# # saving the dataframe
# df.to_csv('data.csv', index=False)

df = pandas.read_csv("files/bcgold.csv")
bitcoin = df['bitcoin'].to_list()
gold = df['gold'].to_list()
bitcoin_pred = []
gold_pred = []
for i in range(0, len(bitcoin)-7):
    avg_bit = sum([bitcoin[i],bitcoin[i+1],bitcoin[i+2],bitcoin[i+3],bitcoin[i+4],bitcoin[i+5],bitcoin[i+6]])/7
    bitcoin_pred.append(avg_bit)
    avg_gold = sum([gold[i], gold[i + 1], gold[i + 2], gold[i + 3], gold[i + 4], gold[i + 5], gold[i + 6]]) / 7
    gold_pred.append(avg_gold)
bitcoin_pred.extend([0,0,0,0,0,0,0])
gold_pred.extend([0,0,0,0,0,0,0])

df['pred_bidcoin'] = bitcoin_pred
df['pred_gold'] = gold_pred

df.to_csv('files/simulation.csv',index=False)
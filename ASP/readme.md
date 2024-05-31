# Advanced Stock Pair

두 주식 쌍에 기반하여 주식을 매매하나 주식에 영향을 주는 제3의 주식의 가격을 참고하여 매매한다.

## Reinforce learning Feeding system
### SK Hynix with Hanmi Semiconductor, with the affective stock is Nvidia
Max Profit : 15%  
End Profit : 10%  
Days of Trade : 20  
``` python
logprofit_shift = 90
reward = 1 if correct else 0

if log_profit < 0 and action == 0: 
    reward += 0.3
elif log_profit > 0.3 and action != 0:
    reward += 0.7
elif log_profit > 0 and action == 0:
    reward = 0
```
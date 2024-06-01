# Affective Stock Pair
## How does ASP Work?
* Specimen Stock pair : SK Hynix & Hanmi Semiconductor  

Loss and Profit Range : -10% to 20%  
**Best : 19.64%**  
**Worst : -6%**  

It is the same way that get two stocks and make them a pair to trade. However ASP includes another factor, the most trendy related stock.  
The related stock, called *Affective Stock* is be followed by stock pair trading. A pair of stocks would sometimes be traded by *Affective System's Decision Making*. Let's check out ASP.  

Affective System is react and trade by the third stock's price.

## Difference Between Normal Stock Pair Algorithm and ASP
**Normal : 14.1%**  
![Normal](./images/NSP%20vs%20Nvda.png)  

> While Normal Stock Pair trading algorithm trading, total net wealth is usually go under the chart of Nvidia.    
> Only when Nvidia goes up, it sparks. However, it wouldn't happen even Nvidia gradually goes up.  
> But, otherwise there's no big plunge even though Nvidia does under go plunge. Because it doesn't reference Nvidia stock price.

**Affective : 12.04%**  
![ASP](./images/ASP%20vs%20Nvda.png)  

> ASP references Nvidia price. When DQN learning, Nvidia's log profit is calculated and it is applied while rewarding. So, Net wealth chart looks following Nvidia's chart.  
> With *Affective System*, even AI orders 'hold', We already know if the related stock, *Affected Stock*, goes up, then both of stock pair's elements would rise.  
> The moment that *Affected System* works could be seemed to nosiy. Look at the points that net wealth cross over Nvidia. The System know in advance and reacts Nvidia would rise or fall.

## Reinforce learning Feeding system
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
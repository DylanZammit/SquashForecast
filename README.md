# Squash Predictor
## Idea
This project attempts to predict the remaining scores of the squash divisions from [SportyHQ](https://www.sportyhq.com/club/box/view/60) using only data from the games played up till the current point in time. The league games are scraped, converted to dataframes and cleaned automatically. In practice, this method can be used in any round robin setting such as the Premier League.

DISCLAIMER: I am _not_ claiming that this is in any way accurate or mathematically sound, but it is simply a simple idea I had which I wanted to implement.
## Scoring System
The games are best of 5, but, all 5 games are played regardless if you win or not. This is because each game won results in a point. Another point is awarded for playing the game, regardless of the score, and another point is awarded to the winning player. The maximum number of points awarded to a single game is thus 7 points: 5 points for each game won in the 5-0 result, a point for winning, and another for simply playing. The minimum number of points is obviously 1 point, just for playing. 
## How it works
If team A beats team C, and in turn C beats B, both by a wide margin, it is natural to expect team A to beat team B. On the other hand, if team B loses by the same margin against both teams A and C, then this essentially gives us no info about the result of A versus B. Mathemtically speaking, we expect "winning" to be transitive (i.e. IF A > C AND C > B THEN A > B). We shall denote "A beats B" by A > B henceforth. This is by no means true in the real world, and there are a multitude of other reasons why a score can go both ways, but this assumption is central to this "forecast" method.

In this squash league, there are 6 possible outcomes: 0-5, 1-4, 2-3, 3-2, 4-1 and 5-0. If A > C by 4 points to 1, then we map this to (an arbitrarily chosen probability) 74% through the function 
```score2prob(s) = s*0.8/5+0.1.```
This means that we expect A > C in the future with a probability of p=74%. Now suppose that C > B by 3-2, so that q=58%. Then assuming transitivity, the probability that A > B is
```Q = pq/(pq+(1-p)(1-q)),```
In other words, `Q` is the probability that A > C and B > C over the probability that A < C and B < C. If, hypothetically speaking, A = C and C = B (drawn) and so p=q=0.5, then we have Q=0.5 since we have no information.

The division table is essentially a lower triangular matrix and can be viewed as a graph. Suppose that we want to predict the score of A versus B. Then we need to find all acyclic paths `P_1, P_2,....,P_N` from A to B in this graph, ex. A->D->C->B, where A already played against D, and same goes for DvC and CvB. The above procedure is iteratively applied to produce the probabilities `Q_1, Q_2, ..., Q_N`. The average of these probabilities is taken to produce `Q`: our supposed probability that A > B.

Finally this probability `Q` is mapped back to a score by applying the inverse transformation of score2prob, and rounding to the nearest integer.

## Example
At the time of writing, the Division 6 is as follows, with blanks meaning that the games are unlpayed yet.
|          | Dylan | Miguel | James | Denis | Chris | Julio | Nick | Genovese | SCORES |
|----------|:-----:|:------:|:-----:|:-----:|-------|-------|------|----------|--------|
|   Dylan  | -   | 1-4    |    | 3-2   | 4-1   | 3-2   | 3-2  |       | 23     |
|  Miguel  | 4-1   | -    | 1-4   |    | 3-2   | 2-3   |   |       | 16     |
|   James  |    | 4-1    | -   | 4-1   |    |    |   |       | 12     |
| Denis    | 2-3   |     | 1-4   | -   | 3-2   |    |   |       | 10     |
| Chris    | 1-4   | 2-3    |    | 2-3   | -   |    |   |       | 8      |
| Julio    | 2-3   | 3-2    |    |    |    | -   |   |       | 8      |
| Nick     | 2-3   |     |    |    |    |    | -  |       | 3      |
| Vito |    |     |    |    |    |    |   | -      | 0      |
Running the script, one will see that the final rpedicting standings along with the results is as follows
| |James    | Miguel | Dylan | Julio | Denis | Genovese | Nick | Chris | SCORES |      
|----------|:------:|:-----:|:-----:|:-----:|----------|------|-------|--------|------|
|   James  | -   | 4-1   | 4-1   | 4-1   | 4-1      | 2.5-2.5  | 4-1   | 4-1    | 39.5 |
|  Miguel  | 1-4    | -  | 4-1   | 2-3   | 3-2      | 2.5-2.5  | 3-2   | 3-2    | 29.5 |
|   Dylan  | 1-4    | 1-4   | - | 3-2   | 3-2      | 2.5-2.5  | 3-2   | 4-1    | 28.5 |
| Julio    | 1-4    | 3-2   | 2-3   | - | 3-2      | 2.5-2.5  | 3-2   | 3-2    | 28.5 |
| Denis    | 1-4    | 2-3   | 2-3   | 2-3   | -     | 2.5-2.5  | 3-2   | 3-2    | 24.5 |
| Vito | 2.5-2.5    | 2.5-2.5   | 2.5-2.5   | 2.5-2.5   | 2.5-2.5      | - | 2.5-2.5   | 2.5-2.5    | 24.5 |
| Nick     | 1-4    | 2-3   | 2-3   | 2-3   | 2-3      | 2.5-2.5  | -  | 3-3    | 22.5 |
| Chris    | 1-4    | 2-3   | 1-4   | 2-3   | 2-3      | 2.5-2.5  | 2-3   | -   | 19.5 |
Some things to note, if there are no possible paths from player A to player B, then 2.5 points are awarded for each player, and the extra point for winning is split up between each player. Since Vito has not played against anyone yet, there is no information to indicate whether or not they will win any games against anyone.

Although Dylan has won 4 out of the 5 games, he is still not forecast to win the division. This is because James, although played fewer games, beat both of his games. Particularly his 4-1 defeat against Miguel strongly suggests that James > Dylan. This is because we have James > Miguel > Dylan in previous games.

[![N|Solid](https://cldup.com/dTxpPi9lDf.thumb.png)](https://nodesource.com/products/nsolid)

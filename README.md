# Imitation Learning over Heterogeneous Agents with Restraining Bolts 
## Additional case study: Breakout-Pong

Implementation of an additional study case from the paper ["Imitation Learning over Heterogeneous Agents with Restraining Bolts."](https://www.dis.uniroma1.it/~degiacom/papers/2020/icaps2020dfip.pdf)(De Giacomo et all, 2020)

## New addition: **Breakout-Pong**



![](./experiments/breakout-pong-output-5-columns/expert/videos/columns5-expert.gif)
![](./experiments/breakout-pong-output-5-columns/learner/videos/columns5-learner.gif)

# Setup
Tested in Ubuntu 18.04.


## Set up environment
Set up virtual environment, and install additional dependencies. The repository includes a basic prepared environment, accessible through `pipenv`, which we encourage to use to handle the libraries.

* Clone this repository:

`git clone https://github.com/ArciAndres/ImitationLearningRestrainingBolts.git`  
`cd ImitationLearningRestrainingBolts`

* Create a virtual environment:
  
`pip install pipenv`  
`pipenv --python=python3.7`  
`pipenv install`

* Activate the virtual environment:

`pipenv shell`



## Credits

This code is strongly based in the repository from the reference paper:  
https://github.com/whitemech/Imitation-Learning-over-Heterogeneous-Agents-with-Restraining-Bolts


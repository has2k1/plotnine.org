from plotnine import * #skip
from plotnine.data import anscombe_quartet #skip
#skip
ggplot(anscombe_quartet, aes(x="x", y="y")) + geom_point()

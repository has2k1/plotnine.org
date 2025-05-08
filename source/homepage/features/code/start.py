from plotnine import * #skip
from plotnine.data import anscombes_quartet #skip
#skip
ggplot(anscombes_quartet, aes(x="x", y="y")) + geom_point()
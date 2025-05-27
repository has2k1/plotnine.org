(
    ggplot(anscombes_quartet, aes("x", "y"))
    + geom_point(color="sienna", fill="orange", size=3)
    + geom_smooth(method="lm", se=False, fullrange=True,
                  color="steelblue", size=1)
    + facet_wrap("dataset")
    + labs(title="Anscombe’s Quartet")
    + scale_y_continuous(breaks=(4, 8, 12))
    + coord_fixed(xlim=(3, 22), ylim=(2, 14))
    + theme_tufte(base_family="Futura", base_size=16)
    + theme(
        axis_line=element_line(color="#4d4d4d"),
        axis_ticks_major=element_line(color="#00000000"),
        axis_title=element_blank(),
        panel_spacing=0.09,
    )
)
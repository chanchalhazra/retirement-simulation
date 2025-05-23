import pandas as pd

def rate_table():

    single_rate_df = pd.DataFrame([[10, 0, 11600], [12, 11600, 47150], [22, 47150, 100525], [24, 100525, 191950],
                  [32, 191950, 243725], [35, 243725, 609350], [37, 609350, 20000000]],columns=["rate", "from$", "To$"])

    married_rate_df = pd.DataFrame([[10, 0, 23200], [12, 23200, 94300], [22, 94300, 201050], [24, 201050, 383900],
                    [32, 383900, 487450], [35, 487450, 731200],[35, 731200, 20000000]], columns=["rate", "from$", "To$"])
    return single_rate_df, married_rate_df


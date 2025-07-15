import mlflow.pyfunc
import pandas as pd
import joblib

class SkforecastWrapper(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        self.forecaster = joblib.load(context.artifacts["model"])

    def predict(self, context, model_input: pd.DataFrame) -> pd.Series:
        """
        model_input: DataFrame with exogenous variables. It must contain the same
                     columns as used during training (`forecaster.exog_names_in_`)
        """
        steps = len(model_input)
        return self.forecaster.predict(steps=steps, exog=model_input)

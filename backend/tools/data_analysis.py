"""
Nexus AI - Data Analysis Tool
Analyze datasets using pandas
"""

import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from tools.base_tool import BaseTool


class DataAnalysisTool(BaseTool):
    """
    Data analysis tool using pandas.
    
    Capabilities:
    - Descriptive statistics
    - Correlation analysis
    - Data cleaning
    - Grouping and aggregation
    """
    
    def __init__(self):
        super().__init__(
            name="data_analysis",
            description="Analyze datasets with descriptive statistics and insights",
            parameters={
                "action": "Analysis type: describe, correlate, group_by, clean (required)",
                "data": "Data as dict, list, or CSV string (required)"
            }
        )
        
        # Try to import pandas
        try:
            import pandas as pd
            import numpy as np
            self.pd = pd
            self.np = np
            self.available = True
        except ImportError:
            self.available = False
            print("⚠️ pandas not available - DataAnalysisTool limited")
    
    def execute(
        self, 
        action: str, 
        data: Any,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute data analysis.
        
        Args:
            action: Type of analysis
            data: Dataset to analyze
            **kwargs: Additional parameters
            
        Returns:
            Analysis results
        """
        if not self.available:
            return {
                "success": False,
                "error": "pandas not installed. Run: pip install pandas numpy",
                "data": None
            }
        
        try:
            # Load data into DataFrame
            df = self._load_data(data)
            
            if df is None or df.empty:
                return {
                    "success": False,
                    "error": "Could not load data or data is empty",
                    "data": None
                }
            
            # Route to appropriate method
            if action == "describe":
                result = self._describe_data(df)
            elif action == "correlate":
                result = self._analyze_correlations(df)
            elif action == "group_by":
                result = self._group_data(df, kwargs.get("group_col"), kwargs.get("agg_col"))
            elif action == "clean":
                result = self._clean_data(df, kwargs.get("strategy", "drop"))
            elif action == "summary":
                result = self._full_summary(df)
            else:
                result = self._describe_data(df)
            
            return {
                "success": True,
                "data": result,
                "action": action
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    def _load_data(self, source: Any):
        """
        Load data into pandas DataFrame.
        """
        if isinstance(source, self.pd.DataFrame):
            return source
        
        if isinstance(source, dict):
            return self.pd.DataFrame(source)
        
        if isinstance(source, list):
            return self.pd.DataFrame(source)
        
        if isinstance(source, str):
            # Try to parse as CSV
            try:
                from io import StringIO
                return self.pd.read_csv(StringIO(source))
            except:
                pass
            
            # Try to parse as JSON
            try:
                return self.pd.read_json(source)
            except:
                pass
        
        return None
    
    def _describe_data(self, df) -> Dict[str, Any]:
        """
        Generate descriptive statistics.
        """
        # Basic info
        shape = df.shape
        columns = list(df.columns)
        dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
        
        # Missing values
        missing = df.isnull().sum().to_dict()
        
        # Numeric statistics
        numeric_cols = df.select_dtypes(include=[self.np.number]).columns
        stats = {}
        
        for col in numeric_cols:
            stats[col] = {
                "mean": round(df[col].mean(), 2) if not df[col].isnull().all() else None,
                "median": round(df[col].median(), 2) if not df[col].isnull().all() else None,
                "std": round(df[col].std(), 2) if not df[col].isnull().all() else None,
                "min": round(df[col].min(), 2) if not df[col].isnull().all() else None,
                "max": round(df[col].max(), 2) if not df[col].isnull().all() else None
            }
        
        # Sample rows
        sample = df.head(5).to_dict(orient="records")
        
        return {
            "shape": {"rows": shape[0], "columns": shape[1]},
            "columns": columns,
            "dtypes": dtypes,
            "missing_values": missing,
            "statistics": stats,
            "sample_rows": sample
        }
    
    def _analyze_correlations(self, df) -> Dict[str, Any]:
        """
        Calculate correlation matrix.
        """
        numeric_df = df.select_dtypes(include=[self.np.number])
        
        if numeric_df.empty:
            return {
                "correlations": {},
                "strong_correlations": [],
                "note": "No numeric columns found"
            }
        
        corr_matrix = numeric_df.corr()
        
        # Find strong correlations
        strong = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                corr_val = corr_matrix.iloc[i, j]
                
                if abs(corr_val) > 0.7:
                    strong.append({
                        "columns": [col1, col2],
                        "correlation": round(corr_val, 3),
                        "strength": "strong positive" if corr_val > 0 else "strong negative"
                    })
        
        return {
            "correlations": corr_matrix.round(3).to_dict(),
            "strong_correlations": strong
        }
    
    def _group_data(
        self, 
        df, 
        group_col: str = None, 
        agg_col: str = None
    ) -> Dict[str, Any]:
        """
        Group and aggregate data.
        """
        if not group_col:
            # Find a categorical column
            cat_cols = df.select_dtypes(include=['object', 'category']).columns
            group_col = cat_cols[0] if len(cat_cols) > 0 else df.columns[0]
        
        if not agg_col:
            # Find a numeric column
            num_cols = df.select_dtypes(include=[self.np.number]).columns
            agg_col = num_cols[0] if len(num_cols) > 0 else None
        
        if agg_col:
            grouped = df.groupby(group_col)[agg_col].agg(['count', 'mean', 'sum'])
            result = grouped.round(2).to_dict()
        else:
            grouped = df.groupby(group_col).size()
            result = {"count": grouped.to_dict()}
        
        return {
            "grouped_by": group_col,
            "aggregated_column": agg_col,
            "results": result
        }
    
    def _clean_data(self, df, strategy: str = "drop") -> Dict[str, Any]:
        """
        Clean data by handling missing values.
        """
        original_rows = len(df)
        missing_before = df.isnull().sum().sum()
        
        if strategy == "drop":
            cleaned = df.dropna()
        elif strategy == "fill_mean":
            numeric_cols = df.select_dtypes(include=[self.np.number]).columns
            cleaned = df.copy()
            cleaned[numeric_cols] = cleaned[numeric_cols].fillna(cleaned[numeric_cols].mean())
        elif strategy == "fill_median":
            numeric_cols = df.select_dtypes(include=[self.np.number]).columns
            cleaned = df.copy()
            cleaned[numeric_cols] = cleaned[numeric_cols].fillna(cleaned[numeric_cols].median())
        elif strategy == "fill_zero":
            cleaned = df.fillna(0)
        else:
            cleaned = df.dropna()
        
        return {
            "original_rows": original_rows,
            "cleaned_rows": len(cleaned),
            "rows_removed": original_rows - len(cleaned),
            "missing_before": int(missing_before),
            "missing_after": int(cleaned.isnull().sum().sum()),
            "strategy_used": strategy
        }
    
    def _full_summary(self, df) -> Dict[str, Any]:
        """
        Generate comprehensive summary.
        """
        desc = self._describe_data(df)
        corr = self._analyze_correlations(df)
        
        return {
            "overview": desc,
            "correlations": corr,
            "insights": self._generate_insights(desc, corr)
        }
    
    def _generate_insights(self, desc: Dict, corr: Dict) -> List[str]:
        """
        Generate simple insights from data.
        """
        insights = []
        
        # Check for missing data
        total_missing = sum(desc.get("missing_values", {}).values())
        if total_missing > 0:
            insights.append(f"⚠️ Dataset has {total_missing} missing values that may need handling")
        
        # Check for strong correlations
        strong_corr = corr.get("strong_correlations", [])
        if strong_corr:
            insights.append(f"📊 Found {len(strong_corr)} strong correlations between variables")
        
        # Dataset size
        shape = desc.get("shape", {})
        insights.append(f"📁 Dataset contains {shape.get('rows', 0)} rows and {shape.get('columns', 0)} columns")
        
        return insights

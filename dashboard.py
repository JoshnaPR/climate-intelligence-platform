#Climate Risk Dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configure page
st.set_page_config(
    page_title="Climate Risk Intelligence Platform",
    page_icon="🌍",
    layout="wide"
)

# Dashboard header
st.title("🌍 Climate Risk Intelligence Platform")
st.markdown("**Climate Risk Assessment with 30+ Major Corporations**")

# Load data
@st.cache_data
def load_enhanced_data():
    """Load our climate risk analysis data"""
    try:
        enhanced_risk = pd.read_csv('data/enhanced_risk_analysis.csv')
        enhanced_financial = pd.read_csv('data/enhanced_financial_data.csv')
        time_series = pd.read_csv('data/time_series_climate_data.csv')
        time_series['date'] = pd.to_datetime(time_series['date'])
        return enhanced_risk, enhanced_financial, time_series
    except FileNotFoundError:
        st.error("Data files not found. Please run the analysis first.")
        return None, None, None

# Load the data
risk_data, financial_data, time_series_data = load_enhanced_data()

if risk_data is not None:
    
    # Sidebar filters
    st.sidebar.header("Dashboard Filters")
    
    # Sector filter
    sectors = ['All'] + sorted(risk_data['sector'].unique().tolist())
    selected_sector = st.sidebar.selectbox("Select Sector", sectors)
    
    # Risk category filter
    risk_categories = ['All'] + sorted(risk_data['risk_category'].unique().tolist())
    selected_risk = st.sidebar.selectbox("Select Risk Level", risk_categories)
    
    # Market cap filter
    min_market_cap = st.sidebar.slider(
        "Minimum Market Cap (Billions)", 
        0, 
        int(risk_data['market_cap_billions'].max()), 
        0
    )
    
    # Filter data
    filtered_data = risk_data.copy()
    
    if selected_sector != 'All':
        filtered_data = filtered_data[filtered_data['sector'] == selected_sector]
    
    if selected_risk != 'All':
        filtered_data = filtered_data[filtered_data['risk_category'] == selected_risk]
    
    filtered_data = filtered_data[filtered_data['market_cap_billions'] >= min_market_cap]
    
    # Key Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Companies Analyzed", 
            len(filtered_data),
            delta=f"{len(filtered_data) - len(risk_data)} from total"
        )
    
    with col2:
        avg_risk = filtered_data['composite_risk'].mean()
        st.metric(
            "Average Risk Score", 
            f"{avg_risk:.1f}",
            delta=f"{avg_risk - risk_data['composite_risk'].mean():.1f} vs overall"
        )
    
    with col3:
        high_risk_count = len(filtered_data[filtered_data['composite_risk'] >= 45])
        st.metric(
            "High Risk Companies", 
            high_risk_count,
            delta=f"{high_risk_count / len(filtered_data) * 100:.1f}% of selection"
        )
    
    with col4:
        total_market_cap = filtered_data['market_cap_billions'].sum()
        st.metric(
            "Total Market Cap", 
            f"${total_market_cap:.1f}B",
            delta=f"{total_market_cap / risk_data['market_cap_billions'].sum() * 100:.1f}% of total"
        )
    
    with col5:
        avg_esg = filtered_data['esg_score'].mean()
        st.metric(
            "Average ESG Score",
            f"{avg_esg:.1f}",
            delta=f"{avg_esg - risk_data['esg_score'].mean():.1f} vs overall"
        )
    
    # Charts Section
    st.header("Risk Analysis Dashboard")
    
    # Row 1: Risk distribution and enhanced sector analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Climate Risk by Company")
        
        chart_data = filtered_data.sort_values('composite_risk', ascending=True)
        
        color_map = {
            'Extreme Risk': '#8B0000',
            'Critical Risk': '#d63031',
            'High Risk': '#e17055',
            'Medium Risk': '#fdcb6e',
            'Low Risk': '#6c5ce7',
            'Minimal Risk': '#00b894'
        }
        
        fig1 = go.Figure(data=[
            go.Bar(
                y=chart_data['symbol'],
                x=chart_data['composite_risk'],
                text=chart_data['composite_risk'].round(1),
                textposition='auto',
                marker_color=[color_map.get(risk, '#666666') for risk in chart_data['risk_category']],
                orientation='h',
                hovertemplate='<b>%{y}</b><br>Risk Score: %{x}<br>Category: %{customdata}<extra></extra>',
                customdata=chart_data['risk_category']
            )
        ])
        
        fig1.update_layout(
            height=600,
            xaxis_title='Risk Score',
            yaxis_title='Company',
            showlegend=False
        )
        
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("Multi-Dimensional Risk Analysis by Sector")
        
        sector_stats = filtered_data.groupby('sector').agg({
            'composite_risk': 'mean',
            'stranded_asset_risk': 'mean',
            'supply_chain_risk': 'mean',
            'regulatory_risk': 'mean'
        }).round(1).reset_index()
        
        fig2 = go.Figure()
        
        fig2.add_trace(go.Bar(
            name='Composite Risk',
            x=sector_stats['sector'],
            y=sector_stats['composite_risk'],
            marker_color='steelblue'
        ))
        
        fig2.add_trace(go.Bar(
            name='Stranded Assets',
            x=sector_stats['sector'],
            y=sector_stats['stranded_asset_risk'],
            marker_color='coral'
        ))
        
        fig2.add_trace(go.Bar(
            name='Supply Chain',
            x=sector_stats['sector'],
            y=sector_stats['supply_chain_risk'],
            marker_color='lightgreen'
        ))
        
        fig2.add_trace(go.Bar(
            name='Regulatory',
            x=sector_stats['sector'],
            y=sector_stats['regulatory_risk'],
            marker_color='gold'
        ))
        
        fig2.update_layout(
            height=600,
            xaxis_title='Sector',
            yaxis_title='Risk Score',
            barmode='group',
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    # Row 2: Time series and correlation analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Climate Risk Trends Over Time")
        
        if time_series_data is not None:
            # Select top 5 companies by market cap for clarity
            top_companies = filtered_data.nlargest(5, 'market_cap_billions')['symbol'].tolist()
            ts_filtered = time_series_data[time_series_data['symbol'].isin(top_companies)]
            
            fig3 = px.line(
                ts_filtered,
                x='date',
                y='risk_score',
                color='symbol',
                title='Risk Score Evolution (Top 5 Companies)',
                labels={'risk_score': 'Risk Score', 'date': 'Date'}
            )
            
            fig3.update_layout(height=400)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Time series data not available")
    
    with col2:
        st.subheader("ESG Score vs Climate Risk")
        
        # Simple scatter plot without trendline to avoid statsmodels dependency
        fig4 = px.scatter(
            filtered_data,
            x='esg_score',
            y='composite_risk',
            color='sector',
            size='market_cap_billions',
            hover_data=['symbol', 'name'],
            title='ESG Performance vs Climate Risk'
        )
        
        fig4.update_layout(height=400)
        st.plotly_chart(fig4, use_container_width=True)
    
    # Row 3: Risk heat map and portfolio analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Risk Component Heatmap")
        
        # Create risk component matrix
        risk_components = filtered_data[['symbol', 'physical_risk', 'transition_risk', 
                                       'stranded_asset_risk', 'supply_chain_risk', 'regulatory_risk']].head(10)
        
        risk_matrix = risk_components.set_index('symbol').T
        
        fig5 = px.imshow(
            risk_matrix,
            title='Risk Components by Company (Top 10)',
            color_continuous_scale='RdYlGn_r',
            aspect='auto'
        )
        
        fig5.update_layout(height=400)
        st.plotly_chart(fig5, use_container_width=True)
    
    with col2:
        st.subheader("Market Cap vs Risk Score")
        
        # Fixed chart without volatility merge issues
        fig6 = px.scatter(
            filtered_data,
            x='market_cap_billions',
            y='composite_risk',
            color='sector',
            size='market_cap_billions',
            hover_data=['symbol', 'name', 'esg_score'],
            title='Market Cap vs Climate Risk',
            labels={
                'market_cap_billions': 'Market Cap (Billions USD)',
                'composite_risk': 'Climate Risk Score'
            }
        )
        
        fig6.update_layout(height=400)
        st.plotly_chart(fig6, use_container_width=True)
    
    # Data Table
    st.header("Detailed Analysis")
    
    # Column selection for data
    available_columns = [col for col in filtered_data.columns if col in [
        'symbol', 'name', 'sector', 'market_cap_billions', 'composite_risk', 
        'risk_category', 'physical_risk', 'transition_risk', 'financial_resilience',
        'stranded_asset_risk', 'supply_chain_risk', 'regulatory_risk',
        'esg_score', 'beta', 'volatility', 'ytd_return'
    ]]
    
    display_columns = st.multiselect(
        "Select columns to display",
        available_columns,
        default=['symbol', 'name', 'sector', 'composite_risk', 'risk_category', 'esg_score']
    )
    
    sort_by = st.selectbox(
        "Sort by",
        ['composite_risk', 'market_cap_billions', 'stranded_asset_risk', 
         'supply_chain_risk', 'regulatory_risk', 'esg_score']
    )
    
    sort_order = st.radio("Sort order", ['Descending', 'Ascending'])
    ascending = sort_order == 'Ascending'
    
    # Display data
    if display_columns:
        display_data = filtered_data[display_columns].sort_values(sort_by, ascending=ascending)
        
        st.dataframe(
            display_data,
            use_container_width=True,
            height=400
        )
    
    # Export Options
    st.header("Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="Download Risk Analysis",
            data=csv,
            file_name="enhanced_climate_risk_analysis.csv",
            mime="text/csv"
        )
    
    with col2:
        if time_series_data is not None:
            ts_csv = time_series_data.to_csv(index=False)
            st.download_button(
                label="Download Time Series Data",
                data=ts_csv,
                file_name="climate_risk_time_series.csv",
                mime="text/csv"
            )
    
    with col3:
        sector_summary = filtered_data.groupby('sector').agg({
            'composite_risk': ['mean', 'std'],
            'stranded_asset_risk': 'mean',
            'supply_chain_risk': 'mean',
            'regulatory_risk': 'mean',
            'esg_score': 'mean',
            'symbol': 'count'
        }).round(2)
        
        summary_csv = sector_summary.to_csv()
        st.download_button(
            label="Download Sector Summary",
            data=summary_csv,
            file_name="enhanced_sector_summary.csv",
            mime="text/csv"
        )

else:
    st.error("Please run the analysis to generate the required data files.")
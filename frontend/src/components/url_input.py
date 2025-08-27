# """
# URL Input Component
# Streamlit component for URL input with validation and suggestions
# """
# import streamlit as st
# import re
#             col1, col2 = st.columns([3, 1])
            
#             with col1:
#                 if st.button(
#                     f"🔗 {url[:40]}{'...' if len(url) > 40 else ''}",
#                     key=f"history_{i}",
#                     help=f"Analyzed at {time_str}"
#                 ):
#                     st.session_state.selected_example = url
#                     st.rerun()
#                     st.session_state.analysis_results = history_item['results']
#                     st.rerun()
            
#             with col2:
#                 st.text(time_str)

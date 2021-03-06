"""
Author:         Ho Xiu Qi

Date Completed: 25th Oct 2021
Last Updated:   25th Oct 2021

Description:
> Constants used in the ICT2202 Team Assignment "Digifax" project
"""
# Data Structure Constants
SANITIZED_DATA = "sanitized"
STATS = "stats"
TIMESTAMP = "timestamp"

INBOUND = "incoming"
OUTBOUND = "outgoing"
ALL = "all"

IN = 0
OUT = 1

TOTAL_TXNS = "all_txn"
UNIQ_IN = "incoming_uniq_data"
UNIQ_OUT = "outgoing_uniq_data"
FROM = "from"
TO = "to"

# Case Data Structure template
TEMPLATE = {"casename": str(), "casedescription": str(), "walletaddresses": list(), "walletrelationships": dict(), "data": {SANITIZED_DATA: dict(), STATS: dict()}, "aliases": dict(), "description": dict(), "filename": dict()}
CASE_FILE_EXT = ".json"

# Node Profile Window Dimensions
NPW_WIDTH = 500
NPW_HEIGHT = 300

# Dashboard - Screen (app) ratios
SCREEN_WIDTH = 0.95
SCREEN_HEIGHT = 0.85

# Dashboard - Logical Division (Columns) ratios
WEBPANEL_WIDTH = 0.65
SIDEPANEL_WIDTH = 1 - WEBPANEL_WIDTH - 0.055

# Dashboard - "Filter" Label ratios
FLABEL_HEIGHT = 0.025
FLABEL_WIDTH = 0.05
FLABEL_Y_OFFSET = 0.011

# Dashboard - "Filter" LineEdit ratios
FEDIT_HEIGHT = 0.02
FEDIT_WIDTH = 0.175
FEDIT_Y_OFFSET = 0.013

# Dashboard - "Add Node" PushButton ratios
ANBTN_HEIGHT = 0.025
ANBTN_WIDTH = 0.07
ANBTN_Y_OFFSET = 0.0092

# Dashboard - "Node" List ratios
NLIST_HEIGHT = 0.2

# Dashboard - "Display Order" Label ratios
DOLABEL_HEIGHT = 0.025
DOLABEL_WIDTH = 0.055
DOLABEL_Y_OFFSET = 0.268

# Dashboard - "Display Order Picker" ComboBox ratios
DOPICKER_HEIGHT = 0.077
DOPICKER_WIDTH = 0.095
DOPICKER_Y_OFFSET = 0.244

# Dashboard - "Transaction Type" Label ratios
TTLABEL_HEIGHT = 0.025
TTLABEL_WIDTH = 0.07
TTLABEL_Y_OFFSET = 0.268

# Dashboard - "Transaction Type Picker" ComboBox ratios
TTPICKER_HEIGHT = 0.077
TTPICKER_WIDTH = 0.075
TTPICKER_Y_OFFSET = 0.244

# Dashboard - "Time Start" Label ratios
TSLABEL_HEIGHT = 0.025
TSLABEL_WIDTH = 0.12
TSLABEL_Y_OFFSET = 0.295

# Dashboard - "Time Start Picker" DateTimeEdit ratios
TSPICKER_HEIGHT = 0.02
TSPICKER_WIDTH = 0.095
TSPICKER_Y_OFFSET = 0.298

# Dashboard - "Time End" Label ratios
TELABEL_HEIGHT = 0.025
TELABEL_WIDTH = 0.12
TELABEL_Y_OFFSET = 0.295

# Dashboard - "Time End Picker" DateTimeEdit ratios
TEPICKER_HEIGHT = 0.02
TEPICKER_WIDTH = 0.095
TEPICKER_Y_OFFSET = 0.298

# Dashboard - "Transactions" Label ratios
TFLABEL_HEIGHT = 0.025
TFLABEL_WIDTH = 0.08
TFLABEL_Y_OFFSET = 0.32

# Dashboard - "Transaction Filter" LineEdit ratios
TFEDIT_HEIGHT = 0.02
TFEDIT_WIDTH = 0.253
TFEDIT_Y_OFFSET = 0.323

# Dashboard - "Node" List ratios
TLIST_HEIGHT = 0.58

# Dashboard - Relationship PushButton ratios
RS_BTN_HEIGHT = 0.025
RS_BTN_WIDTH = 0.08
RS_BTN_SPACING = 1.6
RS_BTN_Y_OFFSET = 0.96

# Relationship data structure
ADDR = 0
WEIGHT = 1
# Relationship weight thresholds
LOWER_BOUND = 5
MIDDLE_BOUND = 100
# Relationship weights
LOW_WEIGHT = 1
MEDIUM_WEIGHT = 2
HIGH_WEIGHT = 3


# PyVis Graph Node Defaults
DEFAULT_COLORS = ['#3da831', '#9a31a8', '#3155a8', '#eb4034']
DEFAULT_WEIGHT = 2
ADDR_DISPLAY_LIMIT = 10

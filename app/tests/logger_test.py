from app.core.logger import app_logger, api_logger, error_logger, log_function_call

# Basic logging
app_logger.info("Application started")
app_logger.error("Something went wrong")

# Function call logging
@log_function_call
def my_function(param1, param2):
    return param1 + param2

# API logging
api_logger.info("API request received")



# Error logging with context
try:
    my_function(1, 2)
    raise Exception("Test error")
except Exception as e:
    error_logger.error(f"Operation failed: {str(e)}", exc_info=True)
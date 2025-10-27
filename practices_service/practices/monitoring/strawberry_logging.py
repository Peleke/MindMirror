import json

import strawberry
from loguru import logger
from strawberry.extensions import SchemaExtension


class LoguruStrawberryExtension(SchemaExtension):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # You can add any per-instance initialization here if needed

    def on_operation(self):
        # This code runs before the GraphQL operation (parse, validate, execute)
        try:
            query_vars = self.execution_context.variables
            op_name = self.execution_context.operation_name
            query_string = self.execution_context.query  # Can be large, consider truncation if needed

            # Sanitize query for cleaner logs
            if query_string:
                log_query = " ".join(query_string.split())
            else:
                log_query = "No query string provided"

            logger.info(
                f"GraphQL Operation Starting. "
                f"Operation: {op_name or 'Unknown'}, "
                f"Query: {log_query}, "  # Consider truncating if too verbose for your needs
                f"Variables: {json.dumps(query_vars)}"
            )
        except Exception as e:
            logger.exception(f"Error during LoguruStrawberryExtension on_operation (pre-yield): {e}")

        yield  # Execution of the operation happens here

        # This code runs after the GraphQL operation has finished
        try:
            op_name = self.execution_context.operation_name  # In case it was set during execution
            result = self.execution_context.result
            if result:
                if result.errors:
                    errors_log = []
                    for err in result.errors:
                        try:
                            # err can be an instance of graphql.GraphQLError
                            # or strawberry.types.exceptions.StrawberryGraphQLError
                            if hasattr(err, "formatted"):
                                errors_log.append(err.formatted)
                            else:
                                errors_log.append(
                                    {
                                        "message": err.message,
                                        "path": err.path,
                                        "locations": err.locations,
                                        # Add other relevant fields from err if needed
                                    }
                                )
                        except Exception:
                            errors_log.append(str(err))
                    logger.error(
                        f"GraphQL Operation Failed. "
                        f"Operation: {op_name or 'Unknown'}, "
                        f"Errors: {json.dumps(errors_log)}"
                    )
                else:
                    # Data can be large, consider summarizing or selective logging
                    # log_data = result.data
                    logger.info(
                        f"GraphQL Operation Succeeded. "
                        f"Operation: {op_name or 'Unknown'}"
                        # f", Response Data: {json.dumps(log_data)}" # Uncomment if you want to log response data
                    )
            else:
                logger.warning(f"GraphQL Operation Ended with no result object. Operation: {op_name or 'Unknown'}")
        except Exception as e:
            logger.exception(f"Error during LoguruStrawberryExtension on_operation (post-yield): {e}")

    # Optional: More granular logging if needed
    # def on_parsing_start(self, *, execution_context: ExecutionContext):
    #     logger.debug("GraphQL parsing started...")

    # def on_parsing_end(self, *, execution_context: ExecutionContext):
    #     logger.debug("GraphQL parsing ended.")

    # def on_validation_start(self, *, execution_context: ExecutionContext):
    #     logger.debug("GraphQL validation started...")

    # def on_validation_end(self, *, execution_context: ExecutionContext):
    #     logger.debug("GraphQL validation ended.")

    # def on_error(self, error: Exception, *, execution_context: ExecutionContext):
    #     logger.exception(f"An unexpected error occurred during GraphQL execution. Operation: {execution_context.operation_name or 'Unknown'}, Error: {error}")

    # def resolve(self, _next, root, info, *args, **kwargs):
    #     # For logging individual resolver calls - can be very verbose
    #     # logger.debug(f"Resolving field: {info.field_name} on type: {info.parent_type.name}")
    #     # try:
    #     #     result = _next(root, info, *args, **kwargs)
    #     #     # logger.debug(f"Resolved field: {info.field_name}, Result: {result}")
    #     #     return result
    #     # except Exception as e:
    #     #     logger.error(f"Error resolving field {info.field_name}: {e}")
    #     #     raise
    #     return _next(root, info, *args, **kwargs)

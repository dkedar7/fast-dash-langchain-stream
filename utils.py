from fast_dash import dash
from fast_dash.utils import theme_mapper
from flask import Response, request
import inspect

def derive_streaming_dash_app(fast_app):
    """
    Derives a Dash app from Fast Dash app by stripping out the callbacks and retaining all other properties.
    We do this because Fast Dash app currently don't allow streaming and their callbacks interfere with the 
    JavaScript callbacks needed for streaming.
    """

    # Grab the layout
    layout = fast_app.app.layout

    # Remove the loader element
    layout.children.children[1].children[1].children[1].children[1] = layout.children.children[1].children[1].children[1].children[1].children

    # Define a blank Dash app and set required attributes
    app = dash.Dash(external_stylesheets=[
                theme_mapper(fast_app.theme),
                "https://use.fontawesome.com/releases/v5.9.0/css/all.css",
            ])

    app.app = app
    app.callback_fn = fast_app.callback_fn
    app.layout = layout
    app.title = fast_app.title

    fast_app.layout_object.callbacks(app)

    return app


# Define callbacks for streaming
def add_streaming(app, function, output_number):

    endpoint_label = f"streaming-output{output_number}"
    signature = inspect.signature(app.callback_fn)
    arg_names = [a for a, _ in signature.parameters.items()]
    n_args = len(arg_names)
    
    def stream_output():
        args = request.json.values()
            
        def stream_response():            
            yield from function(*args)
                
        return Response(stream_response(), mimetype="text/response-stream")
    
    func = stream_output
    func.__name__ = f"stream_output{output_number}"
    app.server.add_url_rule(f"/{endpoint_label}", None, func, methods=["POST"])

    # Obtain the streaming JS function
    js_func = generate_javascript_streaming_function(n_args, endpoint_label, f"output-{output_number}")

    # Define clientside callback
    callback_args = [dash.Output(f"output-{output_number}", "children"),
                     dash.Input("submit_inputs", "n_clicks")] + \
                     [dash.State(arg, "value") for arg in arg_names]
        
    dash.clientside_callback(
        js_func,
        *callback_args,       
        prevent_initial_call=True,
    )


def generate_javascript_streaming_function(n_args, endpoint, output_component_id):
    "Generate the streaming JS function from function arguments and ID of the output component"

    function_args = ["n_clicks"] + [f"arg{i+1}" for i in range(n_args)]
    argument_string = ", ".join(function_args)

    payload_string = [f"{arg}: {arg}" for arg in function_args[1:]]
    payload_string = f"{{ {', '.join(payload_string)} }}"

    js_func = f"""
    async function streaming({argument_string}) {{
        const responseWindow = document.querySelector("#{output_component_id}");
        const payload = {payload_string};
        
        const response = await fetch("/{endpoint}", {{
            method: "POST",
            headers: {{
                "Content-Type": "application/json",
            }},
            body: JSON.stringify(payload),
        }});
        
        // Create a new TextDecoder to decode the streamed response text
        const decoder = new TextDecoder();
        
        // Set up a new ReadableStream to read the response body
        const reader = response.body.getReader();
        let chunks = "";
        
        // Read the response stream as chunks and append them to the chat log
        while (true) {{
            const {{ done, value }} = await reader.read();
            if (done) break;
            chunks += decoder.decode(value);
            const htmlText = chunks;
            responseWindow.innerHTML = htmlText;
        }}
        
        // return false to enable the submit button again (disabled=false)
        return false;
        }}
    """

    return js_func

def rename_function(newname):
    def decorator(f):
        f.__name__ = newname
        return f
    return decorator
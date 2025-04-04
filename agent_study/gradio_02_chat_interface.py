import gradio as gr

def echo(message, history):
    return message

# 调整页面布局
css = '''
.gradio-container {max-width:850px !important; margin:20px auto !important;}
.message-container { padding: 10px !important; font-size: 14px; !important; }
'''

demo = gr.ChatInterface(
    fn=echo,
    title="那个她聊天机器人",
    chatbot=gr.Chatbot(height=400, bubble_full_width=False),
    theme=gr.themes.Default(spacing_size='sm', radius_size='sm'),
    textbox=gr.Textbox(placeholder="开始跟她聊天~", container=False, scale=7),
    examples=['在吗', '饿了吗', '一起吗', '等下我'],
    submit_btn=gr.Button('提交', variant='primary'),
    # clear_btn=gr.Button('清空记录'),
    # retry_btn=None,
    # undo_btn=None,
)

if __name__ == "__main__":
    demo.launch(debug=True)
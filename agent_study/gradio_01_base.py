import gradio as gr

# 快速上手
def greet(name):
    return "Hello " + name + "!"

# demo = gr.Interface(greet, inputs='text', outputs='text')

# 修改属性
demo = gr.Interface(
    fn=greet,
    inputs=[
        gr.Text(label="输入:", value='请输入...', lines=5),
        ],
    outputs=[
        gr.Text(label="输出", lines=5),
        ]
)

if __name__ == '__main__':
    demo.launch()
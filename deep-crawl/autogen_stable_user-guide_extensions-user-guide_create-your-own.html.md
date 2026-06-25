<!-- 来源: https://microsoft.github.io/autogen/stable/user-guide/extensions-user-guide/create-your-own.html -->

# 创建您自己的扩展#

借助 0.4 版本中的新包结构，创建和发布您自己的扩展到 AutoGen 生态系统比以往任何时候都更加容易。本页详细介绍了一些最佳实践，以便您的扩展包能够与 AutoGen 生态系统良好集成。

## 最佳实践#

### 命名#

对于命名没有要求。但使用 `autogen-` 作为包名的前缀会使其更易于查找。

### 通用接口#

只要可能，扩展应该实现 `autogen_core` 包中提供的接口。这将为用户提供更一致的体验。

#### 对 AutoGen 的依赖#

为确保扩展与为其设计的 AutoGen 版本兼容，建议在 `pyproject.toml` 的依赖项部分中使用适当的约束来指定 AutoGen 的版本。
    
    
    [project]
    # ...
    dependencies = [
        "autogen-core>=0.4,<0.5"
    ]
    

### 类型提示的使用#

AutoGen 倡导使用类型提示以提供更好的开发体验。扩展应尽可能使用类型提示。

## 发现#

为了让用户更轻松地找到您的扩展、示例、服务或包，您可以将 [主题](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics) [`autogen`](https://github.com/topics/autogen) 添加到 GitHub 仓库。

还提供更具体的主题：

  * [`autogen-extension`](https://github.com/topics/autogen-extension) 用于扩展

  * [`autogen-sample`](https://github.com/topics/autogen-sample) 用于示例

## 从 0.2 的变化#

在 AutoGen 0.2 中，通常将第三方扩展和示例合并到主仓库中。我们非常感谢所有为 0.2 中的生态系统笔记本、模块和页面做出贡献的用户。但是，总的来说，我们正在远离这种模式，以提供更大的灵活性并减少维护负担。

有一个 `autogen-ext` 包用于第一方支持的扩展，但我们希望有选择地管理维护负担。如果您想了解您的扩展是否适合添加到 `autogen-ext` 中，请提交一个问题让我们讨论。否则，我们鼓励您将扩展作为单独的包发布，并遵循发现下的指导，以便用户可以轻松找到它。

__On this page

[ __Edit on GitHub](https://github.com/microsoft/autogen/edit/main/python/docs/src/user-guide/extensions-user-guide/create-your-own.md)

[ __Show Source](../../_sources/user-guide/extensions-user-guide/create-your-own.md.txt)

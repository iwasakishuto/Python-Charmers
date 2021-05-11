# coding: utf-8
def test_DictParamProcessor():
    import argparse
    from pycharmers.utils import DictParamProcessor
    parser = argparse.ArgumentParser()
    parser.add_argument("--dict_params", action=DictParamProcessor)
    args = parser.parse_args(args=["--dict_params", "foo = [a, b, c]", "--dict_params", "bar=d"])
    args.dict_params
    # {'foo': ['a', 'b', 'c'], 'bar': 'd'}
    args = parser.parse_args(args=["--dict_params", "foo=a, bar=b"])
    # ValueError: too many values to unpack (expected 2)


def test_KwargsParamProcessor():
    import argparse
    from pycharmers.utils import KwargsParamProcessor
    parser = argparse.ArgumentParser()
    parser.add_argument("--kwargs", action=KwargsParamProcessor)
    args = parser.parse_args(args=["--kwargs", "foo=a", "--kwargs", "bar=b"])
    (args.kwargs, args.foo, args.bar)
    # (None, 'a', 'b')


def test_ListParamProcessorCreate():
    import argparse
    from pycharmers.utils import ListParamProcessorCreate
    parser = argparse.ArgumentParser()
    parser.add_argument("--list_params", action=ListParamProcessorCreate())
    args = parser.parse_args(args=["--list_params", "[あ, い, う]"])
    args.list_params
    # ['あ', 'い', 'う']


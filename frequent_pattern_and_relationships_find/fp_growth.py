# -*- coding: utf-8 -*-


class TreeNode:
    """ FP 树 """

    def __init__(self, name_value, num_occur, parent_node):
        self.name = name_value
        self.count = num_occur
        self.parent = parent_node
        # {item:treeNode}
        self.children = {}
        # 用于指向相同元素项所在的树节点
        self.node_link = None

    def inc(self, num_occur):
        self.count += num_occur

    def display(self, index=1):
        print
        '---' * index, '|', self.name, ':', self.count
        for child in self.children.values():
            child.display(index + 1)


class FPGrowth:
    def __init__(self, data_set, min_sup=1):
        self.data_set = data_set
        self.min_sup = min_sup

    def __update_header(self, head_node, target_node):
        """
        更新链表
        :param head_node: 链表表头节点
        :param target_node: 需要添加到链表尾部的节点
        :return: 
        """
        while head_node.node_link is not None:
            head_node = head_node.node_link
        head_node.node_link = target_node

    def __update_tree(self, items, in_tree, header_table, count):
        """
        将一条排好序的记录链接到FP树的根节点
        :param items: 排好序的一条记录
        :param in_tree: 要更新的树节点
        :param header_table: 项表头
        :param count: 记录数
        :return: 
        """
        # 若第一项是否已经存在，则更新树节点
        if items[0] in in_tree.children:
            in_tree.children[items[0]].inc(count)
        else:
            # 新添加的树节点
            in_tree.children[items[0]] = TreeNode(items[0], count, in_tree)
            if header_table[items[0]][1] is None:
                # 该项第一次被添加到树中，记录该项元素的链表表头，TreeNode
                header_table[items[0]][1] = in_tree.children[items[0]]
            else:
                # 将该节点添加到链表尾部
                self.__update_header(header_table[items[0]][1], in_tree.children[items[0]])
        if len(items) > 1:
            # 对该条记录剩下的元素项递归调用update_tree
            self.__update_tree(items[1::], in_tree.children[items[0]], header_table, count)

    def __create_fp_tree(self, data_set, min_sup):
        """
        构建FP树
        :return: 
        """
        # 用字典来保存头指针表，除了存放指针外，还用来保存FP树中每类元素的总数
        # {item:3}
        header_table = {}
        ''' 第一次遍历数据集 '''
        # 统计各项的支持度计数
        for trans in data_set:
            for item in trans:
                header_table[item] = header_table.get(item, 0) + data_set[trans]
        # 删除不满足最小支持度阈值的项
        for item in header_table.keys():
            if header_table[item] < min_sup:
                del header_table[item]
        # 频繁一项集
        freq_item_set = set(header_table.keys())
        if len(freq_item_set) == 0:
            return None, None
        # {item:[3,None]}
        for item in header_table:
            # [项支持度计数，该项元素的链表表头]
            header_table[item] = [header_table[item], None]
        # 根节点
        ret_tree = TreeNode('root', 1, None)
        ''' 第二次遍历数据集 '''
        # frozenset, 1
        for tran_set, count in data_set.items():
            # 记录每一条记录各项元素的支持度，用于排序
            local_data = {}
            for item in tran_set:
                if item in freq_item_set:
                    local_data[item] = header_table[item][0]
            if len(local_data) > 0:
                # 按各项的支持度计数从大到小排序 -> list [item]
                ordered_items = [v[0] for v in sorted(local_data.items(), key=lambda p: p[1], reverse=True)]
                self.__update_tree(ordered_items, ret_tree, header_table, count)
        return ret_tree, header_table

    def __ascend_tree(self, leaf_node, prefix_path):
        """
        回溯所给节点的前缀路径
        :param leaf_node: 
        :param prefix_path: 
        :return: 
        """
        if leaf_node.parent is not None:
            prefix_path.append(leaf_node.name)
            self.__ascend_tree(leaf_node.parent, prefix_path)

    def __find_prefix_path(self, tree_node):
        """
        找出所给项的所有条件模式基
        :param tree_node: 
        :return: 
        """
        # 条件模式基
        condition_patterns = {}
        while tree_node is not None:
            prefix_path = []
            self.__ascend_tree(tree_node, prefix_path)
            if len(prefix_path) > 1:
                condition_patterns[frozenset(prefix_path[1:])] = tree_node.count
            tree_node = tree_node.node_link
        return condition_patterns

    def __recursive_fp_tree(self, header_table, min_sup, prefix_path, freq_item_list):
        """
        递归遍历FP树的所有条件FP树
        :param header_table: 
        :param min_sup: 
        :param prefix_path: 
        :param freq_item_list: 
        :return: 
        """
        # 按各项支持度计数从小到大的顺序开始分别挖掘的条件FP树
        find_freq_list = [v[0] for v in sorted(header_table.items(), key=lambda p: p[1])]
        for item in find_freq_list:
            new_freq_set = prefix_path.copy()
            new_freq_set.add(item)
            freq_item_list.append(new_freq_set)
            condition_pattern = self.__find_prefix_path(header_table[item][1])
            condition_fp_tree, new_head_table = self.__create_fp_tree(condition_pattern, min_sup)
            if new_head_table is not None:
                self.__recursive_fp_tree(new_head_table, min_sup, new_freq_set, freq_item_list)

    def get_freq_items(self):
        """
        获取频繁项集
        :return: 频繁项集
        """
        fp_tree, head_table = self.__create_fp_tree(self.data_set, self.min_sup)
        freq_items_list = []
        self.__recursive_fp_tree(head_table, 2, set([]), freq_items_list)
        return freq_items_list


def load_data():
    """
    加载数据
    :return: 
    """
    ret_dict = {}
    simple_data = [
        ['I1', 'I2', 'I5'],
        ['I2', 'I4'],
        ['I2', 'I3'],
        ['I1', 'I2', 'I4'],
        ['I1', 'I3'],
        ['I2', 'I3'],
        ['I1', 'I3'],
        ['I1', 'I2', 'I3', 'I5'],
        ['I1', 'I2', 'I3']
    ]
    for trans in simple_data:
        # frozenset 是不可变的 set 集合
        # 可以直接将其作为字典的 key，也可以作为其他集合的元素。
        # 没有 add 和 remove 方法
        ret_dict[frozenset(trans)] = 1
    return ret_dict


if __name__ == '__main__':
    data = load_data()
    print(FPGrowth(data, 2).get_freq_items())

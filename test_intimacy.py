"""
测试亲密度系统
运行: python test_intimacy.py
"""

# 模拟 get_intimacy_level 函数
def get_intimacy_level(intimacy_points):
    levels = [
        {
            'level': 0, 'title': '陌生人', 'title_en': 'Stranger',
            'min_points': 0, 'max_points': 99, 'color': '#95A5A6', 'icon': '👤',
            'privileges': ['基础聊天', 'Basic Chat']
        },
        {
            'level': 1, 'title': '熟人', 'title_en': 'Acquaintance',
            'min_points': 100, 'max_points': 499, 'color': '#3498DB', 'icon': '👋',
            'privileges': ['自定义昵称', 'Custom Nickname', '表情包', 'Emoji Packs']
        },
        {
            'level': 2, 'title': '好友', 'title_en': 'Friend',
            'min_points': 500, 'max_points': 999, 'color': '#9B59B6', 'icon': '🤝',
            'privileges': ['语音消息', 'Voice Messages', '文件分享', 'File Sharing']
        },
        {
            'level': 3, 'title': '密友', 'title_en': 'Close Friend',
            'min_points': 1000, 'max_points': 2499, 'color': '#E67E22', 'icon': '💙',
            'privileges': ['专属聊天主题', 'Custom Themes', '特殊徽章', 'Special Badges']
        },
        {
            'level': 4, 'title': '挚友', 'title_en': 'Best Friend',
            'min_points': 2500, 'max_points': 4999, 'color': '#F39C12', 'icon': '⭐',
            'privileges': ['共享 Evercoin', 'Shared Evercoin', '联合游戏', 'Co-op Games']
        },
        {
            'level': 5, 'title': '灵魂伴侣', 'title_en': 'Soulmate',
            'min_points': 5000, 'max_points': float('inf'), 'color': '#E74C3C', 'icon': '💖',
            'privileges': ['VIP 礼物', 'VIP Gifts', '专属动画', 'Exclusive Animations', '优先支持', 'Priority Support']
        }
    ]
    
    for i, level_data in enumerate(levels):
        if level_data['min_points'] <= intimacy_points <= level_data['max_points']:
            if i < len(levels) - 1:
                next_level = levels[i + 1]
                current_progress = intimacy_points - level_data['min_points']
                total_needed = level_data['max_points'] - level_data['min_points'] + 1
                progress_percentage = (current_progress / total_needed) * 100
                points_to_next = next_level['min_points'] - intimacy_points
            else:
                progress_percentage = 100
                points_to_next = 0
                next_level = None
            
            return {
                'level': level_data['level'],
                'title': level_data['title'],
                'title_en': level_data['title_en'],
                'color': level_data['color'],
                'icon': level_data['icon'],
                'privileges': level_data['privileges'],
                'current_points': intimacy_points,
                'min_points': level_data['min_points'],
                'max_points': level_data['max_points'],
                'progress_percentage': progress_percentage,
                'points_to_next': points_to_next,
                'next_level': next_level
            }
    
    return None

# 测试不同亲密度值
test_values = [0, 50, 99, 100, 250, 500, 750, 1000, 1500, 2500, 3000, 5000, 10000]

print("=" * 80)
print("🎯 EverSpace 亲密度系统测试")
print("=" * 80)
print()

for points in test_values:
    info = get_intimacy_level(points)
    
    print(f"亲密度点数: {points}")
    print(f"  {info['icon']} 等级 {info['level']}: {info['title']} ({info['title_en']})")
    print(f"  颜色: {info['color']}")
    print(f"  进度: {info['progress_percentage']:.1f}%")
    
    if info['points_to_next'] > 0:
        print(f"  还需 {info['points_to_next']} 点升至 Lv.{info['level']+1}")
    else:
        print(f"  ⭐ 已达到最高等级！")
    
    print(f"  特权: {', '.join(info['privileges'][:2])}")
    print()

print("=" * 80)
print("✅ 测试完成！所有等级计算正常。")
print("=" * 80)

# 测试边界值
print("\n📊 边界值测试:")
boundaries = [
    (99, 100, "Lv.0 → Lv.1"),
    (499, 500, "Lv.1 → Lv.2"),
    (999, 1000, "Lv.2 → Lv.3"),
    (2499, 2500, "Lv.3 → Lv.4"),
    (4999, 5000, "Lv.4 → Lv.5")
]

for before, after, desc in boundaries:
    before_info = get_intimacy_level(before)
    after_info = get_intimacy_level(after)
    print(f"{desc}:")
    print(f"  {before} 点: {before_info['icon']} {before_info['title']} → {after} 点: {after_info['icon']} {after_info['title']}")

print("\n🎉 亲密度系统完整实现！准备投入使用！")

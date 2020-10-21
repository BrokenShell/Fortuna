from Fortuna import min_int, max_int, min_float, max_float, min_above, min_below


if __name__ == '__main__':
    print("\nLocal Platform Limits:")
    print(f"Min Int:   {min_int()}")
    print(f"Max Int:    {max_int()}")
    print(f"Min Float: {min_float()}")
    print(f"Max Float:  {max_float()}")
    print(f"Min Below: {min_below()}")
    print(f"Min Above:  {min_above()}")

import os.path
import os
import stat


class FilePermissions:

    mapping = [stat.S_IRUSR, stat.S_IWUSR, stat.S_IXUSR,
               stat.S_IRGRP, stat.S_IWGRP, stat.S_IXGRP,
               stat.S_IROTH, stat.S_IWOTH, stat.S_IXOTH]

    @classmethod
    def perms_from_stat(cls, val: os.stat_result) -> list:
        ans = [None]*9
        for i in range(9):
            ans[i] = (val.st_mode & cls.mapping[i]) != 0
        return ans

    @classmethod
    def int_from_perms(cls, val: list) -> int:
        ans = 0
        for i in range(9):
            ans |= val[i]*cls.mapping[i]
        return ans

"""Conservative Java class canonicalization, not a JVM verifier or equivalence proof.

Specification: JVMS 8 chapters 4 and 6. Unknown attributes/instructions fail closed.
Normalized scope excludes named debug attributes and unused constant-pool entries;
it resolves pool references and instruction addresses, not arbitrary program logic.
"""
from __future__ import annotations

from dataclasses import dataclass
from .dah1 import AuditError, Reader, class_summary

POLICY = "dah-class-normalization-v1"
DEBUG = {"SourceFile", "SourceDebugExtension", "LineNumberTable",
         "LocalVariableTable", "LocalVariableTypeTable"}


class Unsupported(AuditError):
    """No normalized-match claim is permitted for this input."""


def need(ok: bool, message: str) -> None:
    if not ok:
        raise Unsupported(message)


@dataclass
class Member:
    name: str
    descriptor: str
    flags: int
    attributes: list

    @property
    def key(self) -> str:
        return self.name + self.descriptor


class ClassFile:
    def __init__(self, data: bytes):
        class_summary(data)  # Reuse existing structural checks before normalization.
        r = Reader(data)
        r.take(4)
        self.version = (r.u2(), r.u2())
        need(45 <= self.version[1] <= 52, "Class version outside supported 45..52")
        self.pool = [None] * r.u2()
        i = 1
        while i < len(self.pool):
            tag = r.u1()
            if tag == 1:
                value = r.take(r.u2())
            elif tag in (3, 4):
                value = r.take(4)
            elif tag in (5, 6):
                value = r.take(8)
            elif tag in (7, 8):
                value = r.u2()
            elif tag in (9, 10, 11, 12):
                value = (r.u2(), r.u2())
            else:
                raise Unsupported(f"Constant-pool tag {tag} is not supported")
            self.pool[i] = (tag, value)
            i += 2 if tag in (5, 6) else 1
        self.flags = r.u2()
        self.name = self.class_name(r.u2())
        parent = r.u2()
        self.parent = self.class_name(parent) if parent else None
        self.interfaces = [self.class_name(r.u2()) for _ in range(r.u2())]
        self.fields = self.members(r)
        self.methods = self.members(r)
        self.attributes = self.attrs(r)
        r.finish()

    def cp(self, i: int, tags: tuple[int, ...] | None = None):
        need(0 < i < len(self.pool) and self.pool[i] is not None, "Invalid pool reference")
        tag, value = self.pool[i]
        need(tags is None or tag in tags, "Wrong constant-pool reference type")
        return tag, value

    def text(self, i: int) -> str:
        _, value = self.cp(i, (1,))
        try:
            return value.decode("ascii")
        except UnicodeDecodeError as exc:
            raise Unsupported("Non-ASCII identifiers are not supported") from exc

    def class_name(self, i: int) -> str:
        return self.text(self.cp(i, (7,))[1])

    def resolve(self, i: int, tags: tuple[int, ...] | None = None):
        tag, value = self.cp(i, tags)
        if tag in (1, 3, 4, 5, 6):
            return (tag, value.hex())  # Preserve float bits and modified UTF-8 strings.
        if tag in (7, 8):
            return (tag, self.resolve(value, (1,)))
        if tag in (9, 10, 11):
            return (tag, self.resolve(value[0], (7,)), self.resolve(value[1], (12,)))
        if tag == 12:
            return (tag, self.resolve(value[0], (1,)), self.resolve(value[1], (1,)))
        raise Unsupported("Unresolvable pool entry")

    def attrs(self, r: Reader) -> list:
        return [(self.text(r.u2()), r.take(r.u4())) for _ in range(r.u2())]

    def members(self, r: Reader) -> list[Member]:
        result, keys = [], set()
        for _ in range(r.u2()):
            flags, name, desc = r.u2(), self.text(r.u2()), self.text(r.u2())
            need((name, desc) not in keys, "Duplicate member identity")
            keys.add((name, desc))
            result.append(Member(name, desc, flags, self.attrs(r)))
        return result

    def instructions(self, code: bytes):
        """Return resolved instructions and an offset-to-ordinal map."""
        r, items, locations = Reader(code), [], {}
        # Branch/switch arguments are marked until all instruction boundaries exist.
        def branch(offset):
            return ("target", offset)
        while r.pos < len(code):
            start = r.pos
            locations[start] = len(items)
            op, args = r.u1(), []
            if op == 0x10:
                args = [int.from_bytes(r.take(1), "big", signed=True)]
            elif op == 0x11:
                args = [int.from_bytes(r.take(2), "big", signed=True)]
            elif op in (0x12, 0x13, 0x14):
                i = r.u1() if op == 0x12 else r.u2()
                args = [self.resolve(i, (5, 6) if op == 0x14 else (3, 4, 7, 8))]
                if op == 0x13:
                    op = 0x12  # ldc_w differs only in pool-index width.
            elif op in (*range(0x15, 0x1a), *range(0x36, 0x3b), 0xa9):
                args = [r.u1()]
            elif op == 0x84:
                args = [r.u1(), int.from_bytes(r.take(1), "big", signed=True)]
            elif 0x99 <= op <= 0xa8 or op in (0xc6, 0xc7, 0xc8, 0xc9):
                n = 4 if op in (0xc8, 0xc9) else 2
                args = [branch(start + int.from_bytes(r.take(n), "big", signed=True))]
                if op in (0xc8, 0xc9):
                    op -= 0x21  # goto_w/jsr_w -> goto/jsr.
            elif op in (0xaa, 0xab):
                need(not any(r.take((-r.pos) % 4)), "Nonzero switch padding")
                s4 = lambda: int.from_bytes(r.take(4), "big", signed=True)
                default = branch(start + s4())
                if op == 0xaa:
                    low, high = s4(), s4()
                    need(0 < high-low+1 <= (len(code)-r.pos)//4, "Invalid tableswitch range")
                    pairs = [(k, branch(start+s4())) for k in range(low, high+1)]
                else:
                    count = s4()
                    need(0 <= count <= (len(code)-r.pos)//8, "Invalid lookupswitch count")
                    pairs = [(s4(), branch(start+s4())) for _ in range(count)]
                    need(all(pairs[i][0] < pairs[i+1][0] for i in range(len(pairs)-1)),
                         "Unsorted lookupswitch keys")
                args = [default, pairs]
            elif 0xb2 <= op <= 0xb9 or op in (0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                tags = (9,) if op <= 0xb5 else (10,) if op == 0xb6 else (10, 11) if op in (0xb7, 0xb8) else (11,) if op == 0xb9 else (7,)
                args = [self.resolve(r.u2(), tags)]
                if op == 0xb9:
                    count, zero = r.u1(), r.u1()
                    need(count > 0 and zero == 0, "Invalid invokeinterface trailer")
                    args.append(count)
                if op == 0xc5:
                    dims = r.u1()
                    need(dims > 0, "Invalid multianewarray dimensions")
                    args.append(dims)
            elif op == 0xbc:
                args = [r.u1()]
                need(4 <= args[0] <= 11, "Invalid newarray type")
            elif op == 0xc4:
                sub = r.u1()
                need(sub in (*range(0x15, 0x1a), *range(0x36, 0x3b), 0x84, 0xa9), "Invalid wide opcode")
                args = [sub, r.u2()]
                if sub == 0x84:
                    args.append(int.from_bytes(r.take(2), "big", signed=True))
            else:
                need(0 <= op <= 0x0f or 0x1a <= op <= 0x35 or 0x3b <= op <= 0x83
                     or 0x85 <= op <= 0x98 or 0xac <= op <= 0xb1 or op in (0xbe, 0xbf, 0xc2, 0xc3),
                     f"Unsupported/reserved opcode 0x{op:02x}")
            items.append((op, args))
        def resolved(value):
            if isinstance(value, tuple) and len(value) == 2 and value[0] == "target":
                need(value[1] in locations, "Branch does not target an instruction")
                return ("instruction", locations[value[1]])
            if isinstance(value, (list, tuple)):
                return tuple(resolved(v) for v in value)
            return value
        return resolved(items), locations

    def code(self, payload: bytes):
        r = Reader(payload)
        stack, locals_ = r.u2(), r.u2()
        raw = r.take(r.u4())
        instructions, positions = self.instructions(raw)
        def point(offset, end=False):
            if end and offset == len(raw):
                return len(instructions)
            need(offset in positions, "Metadata offset is not an instruction boundary")
            return positions[offset]
        handlers = []
        for _ in range(r.u2()):
            start, end, handler, catch = r.u2(), r.u2(), r.u2(), r.u2()
            need(start < end, "Invalid exception range")
            handlers.append((point(start), point(end, True), point(handler),
                             self.resolve(catch, (7,)) if catch else None))
        attributes = self.normalize_attrs(self.attrs(r), "code", point)
        r.finish()
        return stack, locals_, instructions, tuple(handlers), attributes

    def stack_map(self, r: Reader, point, modern: bool):
        def vtype():
            tag = r.u1()
            need(0 <= tag <= 8, "Invalid verification type")
            return (tag, self.resolve(r.u2(), (7,))) if tag == 7 else (tag, point(r.u2())) if tag == 8 else (tag,)
        frames, previous = [], -1
        for _ in range(r.u2()):
            if not modern:
                offset = r.u2()
                locals_ = tuple(vtype() for _ in range(r.u2()))
                stack = tuple(vtype() for _ in range(r.u2()))
                frames.append((point(offset), locals_, stack))
                continue
            tag = r.u1()
            if tag <= 63:
                delta, kind, locals_, stack = tag, "same", (), ()
            elif tag <= 127:
                delta, kind, locals_, stack = tag-64, "same1", (), (vtype(),)
            elif tag == 247:
                delta, kind, locals_, stack = r.u2(), "same1", (), (vtype(),)
            elif 248 <= tag <= 250:
                delta, kind, locals_, stack = r.u2(), ("chop", 251-tag), (), ()
            elif tag == 251:
                delta, kind, locals_, stack = r.u2(), "same", (), ()
            elif 252 <= tag <= 254:
                delta, kind = r.u2(), "append"
                locals_, stack = tuple(vtype() for _ in range(tag-251)), ()
            elif tag == 255:
                delta, kind = r.u2(), "full"
                locals_ = tuple(vtype() for _ in range(r.u2()))
                stack = tuple(vtype() for _ in range(r.u2()))
            else:
                raise Unsupported("Reserved stack-map frame type")
            previous += delta + 1
            frames.append((point(previous), kind, locals_, stack))
        return tuple(frames)

    def normalize_attrs(self, attributes: list, location: str, point=None):
        result, seen = [], set()
        for name, payload in attributes:
            need(name not in seen, "Duplicate attribute")
            seen.add(name)
            if name in DEBUG:
                continue  # Explicitly outside the normalized scope.
            r = Reader(payload)
            if name == "Code" and location == "method":
                value = self.code(payload); r.take(len(payload))
            elif name == "ConstantValue" and location == "field":
                value = self.resolve(r.u2(), (3, 4, 5, 6, 8))
            elif name == "Exceptions" and location == "method":
                value = tuple(self.resolve(r.u2(), (7,)) for _ in range(r.u2()))
            elif name == "InnerClasses" and location == "class":
                rows = []
                for _ in range(r.u2()):
                    inner, outer, label, flags = r.u2(), r.u2(), r.u2(), r.u2()
                    rows.append((self.resolve(inner, (7,)) if inner else None,
                                 self.resolve(outer, (7,)) if outer else None,
                                 self.resolve(label, (1,)) if label else None, flags))
                value = tuple(rows)
            elif name == "EnclosingMethod" and location == "class":
                owner, method = r.u2(), r.u2()
                value = (self.resolve(owner, (7,)), self.resolve(method, (12,)) if method else None)
            elif name in ("Synthetic", "Deprecated"):
                value = ()
            elif name == "Signature":
                value = self.resolve(r.u2(), (1,))
            elif name in ("StackMap", "StackMapTable") and location == "code":
                value = self.stack_map(r, point, name == "StackMapTable")
            else:
                raise Unsupported(f"Unsupported {location} attribute: {name}")
            r.finish()
            result.append((name, value))
        return tuple(sorted(result))

    def normalized_member(self, member: Member, location="method"):
        return (member.name, member.descriptor, member.flags,
                self.normalize_attrs(member.attributes, location))

    def normalized(self):
        # Declaration ordering, identifiers, flags, limits, versions are preserved.
        return (self.version, self.flags, self.name, self.parent, tuple(self.interfaces),
                tuple(self.normalized_member(f, "field") for f in self.fields),
                tuple(self.normalized_member(m) for m in self.methods),
                self.normalize_attrs(self.attributes, "class"))

nasm -f elf64 result.asm
gcc -no-pie result.o
./a.out 12
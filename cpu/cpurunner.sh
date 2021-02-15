#!/bin/bash

# we run this script on machine and got a average of 20% CPU-usage, which is used to test process_cpu_usage
[[ "$1" == "-h" ]] && exit 1
count=1
count2=1
count3=1
times=100
loops=1000
while (( count < $loops )) ; do
	let count++
	count2=1
	while (( count2 < $times )) ; do
		let count2++
		count3=1
		while (( count3 < $times )) ; do
			let count3++
		done
	done
	date
	sleep 5
done

exit 0

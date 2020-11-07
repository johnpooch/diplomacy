if [ $RUNMIGRATIONS ]; then
    echo Running migrations...
    manage migrate
fi

for target in $WAITFOR; do
    wait-for-it $target --timeout=120
done


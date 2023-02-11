# Parameters
#
# $1 - python-root-list
# $2 - extra-pylint-options

echo python-root-list:          $1
echo extra-pylint-options:      $2

# actions path has the copy of this actions repo
echo $RUNNER_OS
if [ $RUNNER_OS = 'Windows' ]
then
    MATCHERS=$GITHUB_ACTION_PATH\matchers\*.json
else
    MATCHERS=$GITHUB_ACTION_PATH/matchers/*.json
fi
echo $MATCHERS

for matcher in $MATCHERS
do
    echo adding matcher $matcher
    echo "::add-matcher::${matcher}"
done
echo "TERM: changing from $TERM -> xterm"
export TERM=xterm

echo Running: pylint $2 $1

pylint --output-format="colorized" $2 $1
exit_code=$?

if [ "$exit_code" = "0" ]; then
    echo "Pylint ok"
else
    echo "Pylint error"
fi